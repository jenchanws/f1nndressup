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
  const data = JSON.parse(e.data).poll
  Object.keys(data).forEach((cat_id) => {
    const options = data[cat_id][1]
    options.forEach(([name, count, percent], i) => {
      let el = document.querySelector(`#option-${cat_id}-${i + 1} + label`)
      let countEl = el.querySelector(".option-count")
      let percentEl = el.querySelector(".option-percent")
      let barEl = el.querySelector(".percent-bar")

      countEl.textContent = "" + count
      percentEl.textContent = "" + percent

      barEl.style.width = percent + "%"
    })
  })
})
