export class ConfigurationError extends Error {
  readonly exitCode = 2;

  constructor(message: string) {
    super(message);
    this.name = "ConfigurationError";
  }
}

export class InputValidationError extends TypeError {
  constructor(message: string) {
    super(message);
    this.name = "InputValidationError";
  }
}

export class ContractValidationError extends RangeError {
  constructor(message: string) {
    super(message);
    this.name = "ContractValidationError";
  }
}
