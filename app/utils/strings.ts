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