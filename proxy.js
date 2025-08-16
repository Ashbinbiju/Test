const fetch = require('node-fetch');

module.exports = async (req, res) => {
  try {
    const { url, method = 'GET', headers = {}, body } = req.body;

    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    const options = {
      method,
      headers,
      timeout: 10000 // 10 second timeout
    };

    if (body && (method === 'POST' || method === 'PUT')) {
      options.body = typeof body === 'string' ? body : JSON.stringify(body);
    }

    const startTime = Date.now();
    const response = await fetch(url, options);
    const responseTime = Date.now() - startTime;

    let responseData;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      try {
        responseData = await response.json();
      } catch (jsonParseError) {
        console.error('Proxy: Error parsing JSON from target URL:', jsonParseError, 'Raw response text:', await response.text());
        responseData = { message: 'Failed to parse JSON response from target', error: jsonParseError.message };
      }
    } else {
      responseData = await response.text();
    }
    console.log('Proxy: Response from target URL:', responseData);

    return res.status(response.status).json({
      status: response.status,
      statusText: response.statusText,
      data: typeof responseData === 'object' ? responseData : String(responseData),
      responseTime,
      headers: Object.fromEntries(response.headers.entries())
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return res.status(500).json({
      error: error.message || 'An error occurred while making the request'
    });
  }
};
