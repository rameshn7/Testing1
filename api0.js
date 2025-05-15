// Cloudflare Worker code for API emulator
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Parse the incoming request URL
  const url = new URL(request.url)
  
  // Get the video URL parameter
  const videoUrl = url.searchParams.get('url')
  
  if (!videoUrl) {
    return new Response(JSON.stringify({
      error: true,
      message: "URL parameter is required"
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  try {
    // Original API endpoint
    const originalApi = "https://download.kringof.com.tr/api/down.php?url="
    
    // Fetch from the original API
    const apiResponse = await fetch(originalApi + encodeURIComponent(videoUrl))
    const data = await apiResponse.json()
    
    // Check for errors in the original API response
    if (data.error) {
      return new Response(JSON.stringify(data), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Get available media options
    const medias = data.medias || []
    if (medias.length === 0) {
      return new Response(JSON.stringify({
        error: true,
        message: "No media found"
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Select a random media (if multiple options exist)
    const selectedMedia = medias[Math.floor(Math.random() * medias.length)]
    const downloadUrl = selectedMedia.url
    
    // Redirect to the download URL
    return Response.redirect(downloadUrl, 302)
    
  } catch (error) {
    return new Response(JSON.stringify({
      error: true,
      message: error.message,
      original_api: "https://download.kringof.com.tr/api/down.php?url="
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
