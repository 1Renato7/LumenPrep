export function sortByMostRecent<T>(items: readonly T[], getTimestamp: (item: T) => string): T[] {
  return [...items].sort((left, right) => {
    const rightTime = Date.parse(getTimestamp(right));
    const leftTime = Date.parse(getTimestamp(left));

    if (Number.isNaN(rightTime)) return Number.isNaN(leftTime) ? 0 : -1;
    if (Number.isNaN(leftTime)) return 1;
    return rightTime - leftTime;
  });
}
