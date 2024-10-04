/**
 * Converts a hyphenated string (like a URL segment) into a prettified, capitalized version.
 * This function is useful for converting URL-friendly strings into human-readable formats.
 * 
 * @param {string} str - The hyphenated string to be prettified.
 * @returns {string} A prettified and capitalized version of the input string.
 */
export function prettifyUrlProvidedName(str: string): string {
  // Replace one or more hyphens with a single space, then capitalize
  return capitalizeFirstLetter(str.replace(/-+/g, ' '));
}

/**
 * Capitalizes the first letter of each word in the string.
 * This function also trims excess whitespace and normalizes spaces between words.
 * 
 * @param {string} str - The string to be capitalized.
 * @returns {string} A string with the first letter of each word capitalized.
 */
export function capitalizeFirstLetter(str: string): string {
  return str
    .trim() // Remove any leading or trailing whitespace
    .replace(/\s+/g, ' ') // Replace multiple spaces with a single space
    .split(' ') // Split the string into an array of words
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter, lowercase the rest
    .join(' '); // Join the words back into a single string
}

/**
 * Converts a space-separated string into a hyphenated lowercase string.
 * This function is essentially the reverse of prettifyUrlProvidedName.
 * It's useful for converting human-readable strings into URL-friendly formats.
 * 
 * @param {string} str - The space-separated string to be converted.
 * @returns {string} A hyphenated lowercase string, suitable for use in URLs.
 */
export function convertToHyphenatedLowercase(str: string): string {
  return str
    .trim() // Remove any leading or trailing whitespace
    .toLowerCase() // Convert the entire string to lowercase
    .replace(/\s+/g, '-') // Replace one or more spaces with a single hyphen
    .replace(/[^a-z0-9-]/g, ''); // Remove any characters that are not lowercase letters, numbers, or hyphens
}
