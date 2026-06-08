import {
  Tree,
  formatFiles,
  names,
  logger,
  addProjectConfiguration,
} from '@nx/devkit';
import {
  applicationGenerator,
  libraryGenerator,
} from '@nx/angular/generators';
import { configurationGenerator as playwrightConfiguration } from '@nx/playwright';
import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';
import { ModuleGeneratorSchema } from './schema';

/**
 * Journey OS — FE module scaffold (`@journeyos/internal:module`).
 *
 * Document-driven: reads the module `generator-config.yml` and generates the canonical
 * module structure (app entry + libs + tags) per
 * `docs/architecture/frontend/standards/module-pattern.md`.
 *
 * Generated stubs are intentionally self-contained (no `@journeyos/shared/*` imports) so the
 * post-scaffold gate (`nx lint/test/build <module>`) passes before the shared libs exist.
 * The real wiring is done by `/fe-implement` during the P-waves.
 */

interface FeatureCfg {
  name: string;
  lib?: string;
  routes?: string[];
  components?: string[];
  permission?: string;
  pre_context?: boolean;
}

interface ModuleContractCfg {
  key?: string;
  label?: string;
  icon?: string;
  permissions?: string[];
  feature_flags?: Array<{ key: string; defaultState: string }>;
}

interface GeneratorConfig {
  module?: string;
  service?: string; // legacy alias
  shell_route?: string;
  features?: FeatureCfg[];
  module_contract?: ModuleContractCfg;
  tool_contract?: ModuleContractCfg; // legacy alias
  e2e?: { features_path?: string; features?: string[] };
}

/** A project already exists in the workspace (idempotent re-runs skip it). */
function projectExists(tree: Tree, root: string): boolean {
  return tree.exists(`${root}/project.json`);
}

/**
 * The architecture docs (and the module `generator-config.yml`) live at the REPO root
 * (`<repo>/docs/...`), which is OUTSIDE the Nx workspace root (`<repo>/frontend`). The Nx Tree
 * is rooted at the workspace and cannot read outside it, so we read the config via `fs` using an
 * absolute path derived from the repo root (`path.dirname(tree.root)`).
 */
function resolveConfigPath(tree: Tree, mod: string, override?: string): string {
  const repoRoot = path.dirname(tree.root); // <repo>/frontend -> <repo>
  if (override) {
    return path.isAbsolute(override)
      ? override
      : path.join(repoRoot, override);
  }
  return path.join(
    repoRoot,
    'docs',
    'architecture',
    'frontend',
    'modules',
    mod,
    'frontend',
    'frontend-spec',
    'generator-config.yml'
  );
}

function readConfig(absPath: string): GeneratorConfig {
  if (!fs.existsSync(absPath)) {
    logger.warn(
      `[internal:module] generator-config.yml not found at ${absPath} — generating with defaults.`
    );
    return {};
  }
  const raw = fs.readFileSync(absPath, 'utf-8');
  return (yaml.load(raw) as GeneratorConfig) ?? {};
}

export async function moduleGenerator(
  tree: Tree,
  options: ModuleGeneratorSchema
) {
  const mod = names(options.name).fileName; // kebab, e.g. "wrks"
  const Mod = names(options.name).className; // Pascal, e.g. "Wrks"
  const MOD = names(options.name).constantName; // UPPER, e.g. "WRKS"

  const specPath = resolveConfigPath(tree, mod, options.specPath);
  const cfg = readConfig(specPath);
  const contract: ModuleContractCfg =
    cfg.module_contract ?? cfg.tool_contract ?? {};

  const featureLibs = (cfg.features ?? []).map(
    (f) => f.lib ?? `feature-${names(f.name).fileName}`
  );
  // De-dup while preserving order.
  const uniqueFeatureLibs = [...new Set(featureLibs)];

  const prefix = 'jos';
  const appProject = mod;

  // ── 1. App entry (apps/<mod>) ──────────────────────────────────────────────
  if (projectExists(tree, `apps/${mod}`)) {
    logger.info(`[internal:module] apps/${mod} exists — skipping app generation.`);
  } else {
    await applicationGenerator(tree, {
      name: appProject,
      directory: `apps/${mod}`,
      projectNameAndRootFormat: 'as-provided',
      standalone: true,
      routing: true,
      style: 'scss',
      prefix,
      changeDetection: 'OnPush',
      e2eTestRunner: 'none',
      unitTestRunner: 'jest',
      skipTests: false,
      tags: `scope:${mod},type:app`,
      strict: true,
    });
  }

  // ── 2. Libraries (libs/<mod>/*) ────────────────────────────────────────────
  type LibDef = { dir: string; type: string };
  const baseLibs: LibDef[] = [
    { dir: 'data-access', type: 'data-access' },
    { dir: 'access', type: 'domain' },
    { dir: 'integration', type: 'domain' },
    { dir: 'navigation', type: 'domain' },
    { dir: 'ui', type: 'ui' },
    { dir: 'styles', type: 'ui' },
  ];
  const featureLibDefs: LibDef[] = uniqueFeatureLibs.map((dir) => ({
    dir,
    type: 'feature',
  }));

  for (const lib of [...baseLibs, ...featureLibDefs]) {
    const root = `libs/${mod}/${lib.dir}`;
    if (projectExists(tree, root)) {
      logger.info(`[internal:module] ${root} exists — skipping.`);
      continue;
    }
    await libraryGenerator(tree, {
      name: `${mod}-${lib.dir}`,
      directory: root,
      projectNameAndRootFormat: 'as-provided',
      standalone: true,
      style: 'scss',
      prefix,
      changeDetection: 'OnPush',
      unitTestRunner: 'jest',
      skipModule: true,
      tags: `scope:${mod},type:${lib.type}`,
    });
  }

  // ── 3. Module entry as a LIBRARY (libs/<mod>/shell-entry, importPath @journeyos/<mod>) ──
  //     ADR: o Shell importa @journeyos/<mod> — apps Nx não importam outros apps (boundary).
  const entryRoot = `libs/${mod}/shell-entry`;
  if (projectExists(tree, entryRoot)) {
    logger.info(`[internal:module] ${entryRoot} exists — skipping entry lib.`);
  } else {
    await libraryGenerator(tree, {
      name: `${mod}-shell-entry`,
      directory: entryRoot,
      projectNameAndRootFormat: 'as-provided',
      importPath: `@journeyos/${mod}`,
      standalone: true,
      style: 'scss',
      prefix,
      changeDetection: 'OnPush',
      unitTestRunner: 'jest',
      skipModule: true,
      tags: `scope:${mod},type:app`,
    });
    // descarta o componente-amostra; a entry escreve seus próprios arquivos.
    tree.delete(`${entryRoot}/src/lib`);
  }
  writeModuleEntry(tree, { mod, Mod, MOD, contract, cfg });
  // host app (apps/<mod>) apenas carrega a entry lib — alvo buildável/serveável + base do e2e.
  writeHostRoutes(tree, { mod, Mod });

  // ── 4. e2e project (apps/<mod>-e2e) — Playwright specs from the .feature list ──
  await generateE2e(tree, { mod, cfg });

  if (!options.skipFormat) {
    await formatFiles(tree);
  }

  logger.info(
    `[internal:module] Generated module "${mod}": app apps/${mod} + ${
      baseLibs.length + featureLibDefs.length
    } libs (${uniqueFeatureLibs.length} features). ` +
      `Next: register in the Shell (module-descriptors.ts) and run nx lint/test/build ${mod}.`
  );
}

function writeModuleEntry(
  tree: Tree,
  ctx: {
    mod: string;
    Mod: string;
    MOD: string;
    contract: ModuleContractCfg;
    cfg: GeneratorConfig;
  }
) {
  const { mod, Mod, MOD, contract, cfg } = ctx;
  const base = `libs/${mod}/shell-entry/src/lib`;
  const label = contract.label ?? Mod;
  const icon = contract.icon ?? 'apps';
  const route = cfg.shell_route ?? `/${mod}`;
  const perms = contract.permissions ?? [];
  const flags = contract.feature_flags ?? [];

  // Self-contained contract types + data (no @journeyos/shared dependency yet).
  tree.write(
    `${base}/${mod}.contract.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module — safe to edit during /fe-implement.
// Canonical module contract. Types are local stubs until @journeyos/shared exposes them.

export interface ModuleMenuMetadata {
  key: string;
  label: string;
  route: string;
  icon: string;
  deepLinks?: Array<{ label: string; route: string; permission?: string }>;
}
export type ModulePermissionMap = Record<string, string[]>;
export type ModuleFeatureFlags = Record<string, { defaultState: 'enabled' | 'disabled' }>;

export const MODULE_KEY = '${mod}' as const;

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: '${label}',
  route: '${route}',
  icon: '${icon}',
  deepLinks: [],
};
`
  );

  tree.write(
    `${base}/${mod}.permission-map.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
import type { ModulePermissionMap } from './${mod}.contract';

export const ${MOD}_PERMISSION_MAP: ModulePermissionMap = {
${perms.map((p) => `  '${p}': [],`).join('\n')}
};
`
  );

  tree.write(
    `${base}/${mod}.feature-flags.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
import type { ModuleFeatureFlags } from './${mod}.contract';

export const ${MOD}_FEATURE_FLAGS: ModuleFeatureFlags = {
${flags
  .map(
    (f) =>
      `  '${f.key}': { defaultState: '${
        f.defaultState === 'disabled' ? 'disabled' : 'enabled'
      }' },`
  )
  .join('\n')}
};
`
  );

  tree.write(
    `${base}/${mod}.routes.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
import { Routes } from '@angular/router';

export const ${MOD}_ROUTES: Routes = [
  // Sub-routes are filled in by /fe-implement (P-waves), one loadComponent per feature.
];
`
  );

  tree.write(
    `${base}/${mod}.nav.config.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
export const ${MOD}_NAV_CONFIG = {
  key: '${mod}',
  breadcrumbRoot: '${label}',
};
`
  );

  tree.write(
    `${base}/${mod}.bootstrap.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
// init/destroy lifecycle of the module (registration with the Shell, subscriptions).
// Wired to the Access Layer during /fe-implement.

export function ${names(mod).propertyName}ModuleInit(): void {
  // registra MODULE_MENU_METADATA no Shell, assina empresa-context + modelo_acesso_versao
}

export function ${names(mod).propertyName}ModuleDestroy(): void {
  // cancela assinaturas; reset de facades escopadas
}
`
  );

  tree.write(
    `${base}/${mod}.module.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
// Único NgModule do módulo (entry lazy carregado pelo Shell via loadChildren).
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ${MOD}_ROUTES } from './${mod}.routes';

@NgModule({
  imports: [RouterModule.forChild(${MOD}_ROUTES)],
})
export class ${Mod}Module {}
`
  );

  // Self-contained descriptor (ADR-004): the Shell imports this to register the module.
  // Emitted here instead of mutating the Shell, which is not yet a proper Nx app.
  tree.write(
    `${base}/${mod}.descriptor.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module.
// Descriptor consumível pelo Shell (module-descriptors): registro estático + lazy entry.
import { MODULE_MENU_METADATA } from './${mod}.contract';
import { ${MOD}_FEATURE_FLAGS } from './${mod}.feature-flags';
import { ${MOD}_PERMISSION_MAP } from './${mod}.permission-map';

export const ${MOD}_MODULE_DESCRIPTOR = {
  key: '${mod}',
  basePath: '${mod}',
  loadChildren: () => import('./${mod}.module').then((m) => m.${Mod}Module),
  metadata: MODULE_MENU_METADATA,
  flags: ${MOD}_FEATURE_FLAGS,
  permissionMap: ${MOD}_PERMISSION_MAP,
};
`
  );

  // Barrel público da entry lib (consumido pelo Shell via @journeyos/<mod>).
  tree.write(
    `libs/${mod}/shell-entry/src/index.ts`,
    `export * from './lib/${mod}.contract';
export * from './lib/${mod}.permission-map';
export * from './lib/${mod}.feature-flags';
export * from './lib/${mod}.routes';
export * from './lib/${mod}.nav.config';
export * from './lib/${mod}.bootstrap';
export * from './lib/${mod}.module';
export * from './lib/${mod}.descriptor';
`
  );
}

/**
 * O host app (`apps/<mod>`) deixa de hospedar a entry: apenas carrega `@journeyos/<mod>` (lib).
 * Serve como alvo buildável/serveável e base do web-server do e2e.
 */
function writeHostRoutes(tree: Tree, ctx: { mod: string; Mod: string }) {
  const { mod, Mod } = ctx;
  tree.write(
    `apps/${mod}/src/app/app.routes.ts`,
    `// AUTO-GENERATED by @journeyos/internal:module — host carrega a entry lib @journeyos/${mod}.
import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  { path: '', loadChildren: () => import('@journeyos/${mod}').then((m) => m.${Mod}Module) },
];
`
  );
}

/**
 * Generates `apps/<mod>-e2e` (Playwright) with one spec stub per `.feature` declared in the
 * generator-config `e2e.features`. The A5 gate only needs the specs to be discoverable/compile;
 * real flows are implemented in /fe-implement (P9).
 */
async function generateE2e(
  tree: Tree,
  ctx: { mod: string; cfg: GeneratorConfig }
) {
  const { mod, cfg } = ctx;
  const root = `apps/${mod}-e2e`;
  if (projectExists(tree, root)) {
    logger.info(`[internal:module] ${root} exists — skipping e2e.`);
    return;
  }

  addProjectConfiguration(tree, `${mod}-e2e`, {
    root,
    projectType: 'application',
    sourceRoot: `${root}/src`,
    targets: {},
    tags: [`scope:${mod}`, 'type:e2e'],
    implicitDependencies: [mod],
  });

  await playwrightConfiguration(tree, {
    project: `${mod}-e2e`,
    directory: 'src',
    js: false,
    skipFormat: true,
    skipPackageJson: true,
    addPlugin: false,
    linter: 'eslint',
  } as never);

  const features = cfg.e2e?.features ?? [];
  for (const f of features) {
    const specName = f.replace(/\.feature$/, '');
    tree.write(
      `${root}/src/${specName}.spec.ts`,
      `import { test } from '@playwright/test';

// Derivado de frontend/e2e/${f} — cenários implementados em /fe-implement (P9).
test.describe('${specName}', () => {
  test.fixme('cenários de ${f}', async ({ page }) => {
    // TODO: implementar os cenários Gherkin de ${f}
  });
});
`
    );
  }
  logger.info(
    `[internal:module] e2e ${root} criado com ${features.length} spec(s).`
  );
}

export default moduleGenerator;
