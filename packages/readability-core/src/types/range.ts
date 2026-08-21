import { ContractValidationError, InputValidationError } from "./errors.ts";

export type SourceRange = Readonly<{ start: number; end: number }>;

export function assertInputText(input: unknown): asserts input is string {
  if (typeof input !== "string") {
    throw new InputValidationError("input must be a string");
  }
}

export function validateRange(input: string, candidate: unknown): SourceRange {
  if (typeof candidate !== "object" || candidate === null || Array.isArray(candidate)) {
    throw new ContractValidationError("range must be an object");
  }
  const record = candidate as Record<string, unknown>;
  if (Object.keys(record).some((field) => field !== "start" && field !== "end")) {
    throw new ContractValidationError("range contains an unknown field");
  }
  const { start, end } = record;
  if (!Number.isInteger(start) || !Number.isInteger(end)) {
    throw new ContractValidationError("range offsets must be integers");
  }
  const numericStart = start as number;
  const numericEnd = end as number;
  if (numericStart < 0 || numericStart >= numericEnd || numericEnd > input.length) {
    throw new ContractValidationError("range must satisfy 0 <= start < end <= input.length");
  }
  return Object.freeze({ start: numericStart, end: numericEnd });
}

export function rangeFromCodePointOffsets(input: unknown, start: number, end: number): SourceRange {
  assertInputText(input);
  const codePoints = Array.from(input);
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 0 || start >= end || end > codePoints.length) {
    throw new ContractValidationError("code point offsets are outside the input");
  }
  const utf16Start = codePoints.slice(0, start).join("").length;
  const utf16End = codePoints.slice(0, end).join("").length;
  return validateRange(input, { start: utf16Start, end: utf16End });
}
