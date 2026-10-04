/**
 * Sports text utility functions for cleaning broadcast event titles and sanitizing strings.
 */

/**
 * Strip redundant static broadcast timezones and embedded start times from event titles.
 * E.g., "(1:00 PM ET / 12:00 PM CT)", "- 1:00 PM ET", "1:00 PM EST", "4:25 PM PT".
 */
export function cleanEventTitle(rawTitle?: string | null): string {
  if (!rawTitle) return ''
  let cleaned = rawTitle

  // 1. Remove parenthesized or bracketed multi-zone/broadcast times
  // E.g. "(1:00 PM ET / 12:00 PM CT)", "(1:00PM EST / 12:00PM CST)", "(1:00 PM / 12:00 PM)"
  cleaned = cleaned.replace(/\s*[\(\[]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)?\s*(?:[/|\-–—]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)?)+\s*[\)\]]/gi, '')

  // 2. Remove unparenthesized multi-zone broadcast times: "1:00 PM ET / 12:00 PM CT"
  cleaned = cleaned.replace(/\s*(?:[-–—|•@]\s*)?\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)?\s*[/|\-–—]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)/gi, '')

  // 3. Remove single parenthesized time/zone: "(1:00 PM ET)", "(1:00 PM)", "(12:00 PM CT)", "(1:00PM)"
  cleaned = cleaned.replace(/\s*[\(\[]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt|local)?\s*[\)\]]/gi, '')

  // 4. Remove trailing or hyphenated times: " - 1:00 PM ET", " - 12:00 PM", " @ 1:00 PM ET", " | 1:00 PM EST"
  cleaned = cleaned.replace(/\s*[-–—|•@]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt|local)?\b/gi, '')

  // 5. Remove trailing standalone time and time zone at end of string: " 1:00 PM ET", " 1:00PM EST", " 12:00 PM CT"
  cleaned = cleaned.replace(/\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)?\s*$/gi, '')

  // 6. Remove leading times: "1:00 PM ET - ...", "12:00 PM - ..."
  cleaned = cleaned.replace(/^\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)?\s*[-–—|:]\s*/gi, '')

  // 7. Remove standalone timezone suffixes: "(ET)", "[ET]", " - ET"
  cleaned = cleaned.replace(/\s*[\(\[]\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)\s*[\)\]]/gi, '')
  cleaned = cleaned.replace(/\s*[-–—|]\s*(?:et|edt|est|ct|cdt|cst|pt|pdt|pst|mt|mdt|mst|utc|gmt)\b/gi, '')

  // 8. Clean up leftover trailing separators
  cleaned = cleaned.replace(/[\s\-–—|/:]+$/g, '').trim()

  return cleaned
}
