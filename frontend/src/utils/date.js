import { formatDistanceToNow } from "date-fns";

export function formatConversationDate(date) {
  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
  });
}