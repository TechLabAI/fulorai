export interface ModuleGeneratorSchema {
  /** Module key in kebab-case (e.g. wrks, lead). */
  name: string;
  /** Override path to the module generator-config.yml. */
  specPath?: string;
  /** Skip formatting after generation. */
  skipFormat?: boolean;
}
