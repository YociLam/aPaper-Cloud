const RELEASE_ROOT =
  "https://github.com/YociLam/aPaper-Cloud/releases/download/translation-engine-v0.1";

const RELEASE_ASSETS = new Map([
  [
    "/v1/translation/v0.1/assets/macos/arm64/apaper-translation-engine-v0.1-macos-arm64.tar.gz",
    `${RELEASE_ROOT}/apaper-translation-engine-v0.1-macos-arm64.tar.gz`,
  ],
  [
    "/v1/translation/v0.1/assets/macos/x86_64/apaper-translation-engine-v0.1-macos-x86_64.tar.gz",
    `${RELEASE_ROOT}/apaper-translation-engine-v0.1-macos-x86_64.tar.gz`,
  ],
]);

function boundedError(status, code, extraHeaders = {}) {
  return new Response(JSON.stringify({ code }), {
    status,
    headers: {
      "cache-control": "no-store",
      "content-type": "application/json; charset=utf-8",
      "x-content-type-options": "nosniff",
      ...extraHeaders,
    },
  });
}

export default {
  async fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return boundedError(405, "method_not_allowed", { allow: "GET, HEAD" });
    }
    const url = new URL(request.url);
    if (url.search || url.hash) {
      return boundedError(404, "asset_not_found");
    }
    const releaseURL = RELEASE_ASSETS.get(url.pathname);
    if (!releaseURL) {
      return boundedError(404, "asset_not_found");
    }
    return new Response(null, {
      status: 307,
      headers: {
        "cache-control": "public, max-age=300",
        location: releaseURL,
        "x-content-type-options": "nosniff",
      },
    });
  },
};
