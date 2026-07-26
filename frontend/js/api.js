const Api = {
  async request(path, options = {}) {
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    };

    let response;
    try {
      response = await fetch(path, config);
    } catch (error) {
      const networkError = new Error(
        "Network error. Check that the server is running."
      );
      networkError.cause = error;
      throw networkError;
    }

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const message =
        (data && data.error) || `Request failed (${response.status})`;
      const apiError = new Error(message);
      apiError.status = response.status;
      apiError.data = data;
      throw apiError;
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
