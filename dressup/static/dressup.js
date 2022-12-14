let src = new EventSource(streamUrl)

src.addEventListener("poll-start", (e) => {
  if (/create/.test(location.href)) {
    location.href = "/"
  } else {
    location.reload()
  }
})

src.addEventListener("poll-end", (e) => {
  if (!/create/.test(location.href)) {
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

function updateCountdown(secsLeft) {
  if (secsLeft <= 0) {
    document.getElementById("time-left").textContent = "0:00"
    location.href = "/"
    return
  }
  const mins = "" + Math.floor(secsLeft / 60)
  let secs = secsLeft - mins * 60
  secs = secs < 10 ? "0" + secs : "" + secs

  const timeStr = `${mins}:${secs}`
  const timeEl = document.getElementById("time-left")
  timeEl.textContent = timeStr

  setTimeout(() => {
    updateCountdown(secsLeft - 1)
  }, 1000)
}

try {
  const secsLeft = Math.floor((endTime - new Date()) / 1000)
  updateCountdown(secsLeft)
} catch {}

if (document.getElementById("create-form")) {
  let form = document.getElementById("create-form")

  function handleSubmitFilter() {
    let form = document.getElementById("create-form")
    const categoriesSelected = Array.from(
      form.querySelectorAll("input[type=checkbox][name=categories]")
    ).filter((e) => e.checked).length
    const durationSelected =
      Array.from(
        form.querySelectorAll("input[type=radio][name=duration]")
      ).filter((e) => e.checked).length !== 0
    form.querySelector("button[type=submit]").disabled =
      categoriesSelected == 0 || !durationSelected
  }

  handleSubmitFilter()
  form.addEventListener("change", handleSubmitFilter)
}
