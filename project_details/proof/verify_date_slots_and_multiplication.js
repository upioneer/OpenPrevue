// Verification test for TimelineGrid local date slots and venue multiplication

function getLocalDateKey(d) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return year + '-' + month + '-' + day
}

// 1. Test local calendar date evaluation (e.g. Sep 30, 2026, 22:30 CDT)
const now = new Date(2026, 8, 30, 22, 30) // Note: month index 8 is September
const todayDateStr = getLocalDateKey(now)
const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
const tomorrowDateStr = getLocalDateKey(tomorrow)

console.log('Today:', todayDateStr)
console.log('Tomorrow:', tomorrowDateStr)

if (todayDateStr !== '2026-09-30') {
  throw new Error('Today date incorrect: expected 2026-09-30, got ' + todayDateStr)
}
if (tomorrowDateStr !== '2026-10-01') {
  throw new Error('Tomorrow date incorrect: expected 2026-10-01, got ' + tomorrowDateStr)
}

// 2. Test event slot assignments
const testEvents = [
  { id: '1', start_time: '2026-09-30T14:00:00', title: 'Today Afternoon Tour' },
  { id: '2', start_time: '2026-09-30T20:00:00', title: 'Tonight Rock Concert' },
  { id: '3', start_time: '2026-10-01T20:00:00', title: 'Tomorrow Evening Show' },
  { id: '4', start_time: '2026-10-02T20:00:00', title: 'In 2 Days Comedy' },
  { id: '5', start_time: '2026-10-05T14:00:00', title: 'Formula 1 USGP (Oct 5)' }
]

function getSlot(e) {
  const d = new Date(e.start_time)
  const dateKey = getLocalDateKey(d)
  const hour = d.getHours()
  if (dateKey === todayDateStr && hour < 17) return 'today'
  if (dateKey === todayDateStr && hour >= 17) return 'tonight'
  if (dateKey === tomorrowDateStr) return 'tomorrow'
  return 'future'
}

for (const evt of testEvents) {
  const slot = getSlot(evt)
  console.log('Event: "' + evt.title + '" (' + evt.start_time + ') -> Slot: ' + slot)
}

if (getSlot(testEvents[0]) !== 'today') throw new Error('Event 1 must be today')
if (getSlot(testEvents[1]) !== 'tonight') throw new Error('Event 2 must be tonight')
if (getSlot(testEvents[2]) !== 'tomorrow') throw new Error('Event 3 must be tomorrow')
if (getSlot(testEvents[3]) !== 'future') throw new Error('Event 4 (in 2 days) must NOT appear in today/tonight/tomorrow')
if (getSlot(testEvents[4]) !== 'future') throw new Error('Event 5 (Oct 5) must NOT appear in today/tonight/tomorrow')

// 3. Test displayedVenues multiplication logic for vertical mode
console.log('\nTesting displayedVenues row multiplication:')
const baseCounts = [1, 2, 3, 4, 5, 8, 12, 16, 20, 24, 30, 40]
for (const baseLen of baseCounts) {
  const targetMinRows = 36
  const rawRepeats = Math.ceil(targetMinRows / baseLen)
  const repeats = Math.max(2, rawRepeats % 2 === 0 ? rawRepeats : rawRepeats + 1)
  const total = repeats * baseLen
  console.log('  Base venues: ' + baseLen + ' -> repeats: ' + repeats + ' (even: ' + (repeats % 2 === 0) + ') -> total rows: ' + total + ' (>= 36: ' + (total >= 36) + ')')
  if (repeats % 2 !== 0) throw new Error('Repeats must be an even number')
  if (total < 36) throw new Error('Total rows must be >= 36 to fill vertical viewport and ensure infinite scroll')
}

console.log('\n[PASS] All date slot and venue multiplication checks passed successfully!')
