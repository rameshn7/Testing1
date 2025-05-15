addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Parse URL and get video URL parameter
  const url = new URL(request.url)
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
    // Call the original API
    const apiUrl = `https://download.kringof.com.tr/api/down.php?url=${encodeURIComponent(videoUrl)}`
    const response = await fetch(apiUrl)
    const data = await response.json()
    
    // Check for errors or no media
    if (data.error || !data.medias || !Array.isArray(data.medias)) {
      return new Response(JSON.stringify({
        error: true,
        message: "No valid media found"
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Filter MP4 media
    const mp4Medias = data.medias.filter(media => media.extension === "mp4")
    
    if (mp4Medias.length === 0) {
      return new Response(JSON.stringify({
        error: true,
        message: "No MP4 format available"
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      })
    }
    
    // Select random media
    const selectedMedia = mp4Medias[Math.floor(Math.random() * mp4Medias.length)]
    
    // Redirect to download URL
    return Response.redirect(selectedMedia.url, 302)
    
    // Alternatively return JSON response:
    // return new Response(JSON.stringify({
    //   download_url: selectedMedia.url,
    //   quality: selectedMedia.quality,
    //   source: data.source,
    //   title: data.title,
    //   error: false
    // }), {
    //   headers: { 'Content-Type': 'application/json' }
    // })
    
  } catch (error) {
    // Hide original API errors
    return new Response(JSON.stringify({
      error: true,
      message: "Service unavailable"
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
