const Api = {
  async request(path, options = {}) {
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    };

    const response = await fetch(path, config);
    let data = null;

    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const message =
        (data && data.error) || `Request failed (${response.status})`;
      const error = new Error(message);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  },

  get(path) {
    return this.request(path);
  },

  post(path, body) {
    return this.request(path, {
      method: "POST",
      body: JSON.stringify(body || {}),
    });
  },

  patch(path, body) {
    return this.request(path, {
      method: "PATCH",
      body: JSON.stringify(body || {}),
    });
  },
};
