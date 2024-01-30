export function prettifyUrlProvidedName(str: string) {
  const nameWithSpaces = str ? str.replace(/-/g, ' ') : '';

  return nameWithSpaces
    .split('-')
    .map(segment => segment
      .split(/\s+/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
    )
    .join(' ');
}

export function convertToHyphenatedLowercase(str: string): string {
  return str
    .toLowerCase()
    .split(/\s+/)
    .join('-');
}

export function capitaliseFirstLetter(str: string): string {
  return str
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}