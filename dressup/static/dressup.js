let src = new EventSource(streamUrl)

src.addEventListener("poll-start", (e) => {
  if (location.href.test(/create/)) {
    location.href = "/"
  } else {
    location.reload()
  }
})

src.addEventListener("poll-end", (e) => {
  if (!location.href.test(/create/)) {
    location.reload()
  }
})

src.addEventListener("vote", (e) => {
  const data = JSON.parse(e.data)
  console.log(data)
})
