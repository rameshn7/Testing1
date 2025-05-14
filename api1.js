addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Set CORS headers to only allow your specific domain
  const corsHeaders = {
    'Access-Control-Allow-Origin': 'https://allinonevideoplayeronline.blogspot.com/', // Replace with your actual domain
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  // Handle OPTIONS request for CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders
    });
  }

  // Parse the incoming request URL
  const url = new URL(request.url);
  
  // Get the video URL parameter
  const videoUrl = url.searchParams.get('url');
  
  if (!videoUrl) {
    return new Response(JSON.stringify({
      error: true,
      message: "URL parameter is required"
    }), {
      status: 400,
      headers: { 
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }

  try {
    // Original API endpoint
    const originalApi = "https://download.kringof.com.tr/api/down.php?url=";
    
    // Fetch from the original API
    const apiResponse = await fetch(originalApi + encodeURIComponent(videoUrl));
    const data = await apiResponse.json();
    
    // Check for errors in the original API response
    if (data.error) {
      return new Response(JSON.stringify(data), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    // Get available media options
    const medias = data.medias || [];
    if (medias.length === 0) {
      return new Response(JSON.stringify({
        error: true,
        message: "No media found"
      }), {
        status: 404,
        headers: { 
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    // Select a random media (if multiple options exist)
    const selectedMedia = medias[Math.floor(Math.random() * medias.length)];
    const downloadUrl = selectedMedia.url;
    
    // For the redirect response, we need to include CORS headers
    const response = Response.redirect(downloadUrl, 302);
    Object.entries(corsHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
    return response;
    
  } catch (error) {
    return new Response(JSON.stringify({
      error: true,
      message: error.message,
      original_api: "https://download.kringof.com.tr/api/down.php?url="
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}
