// Shell module registry — descritores estáticos dos módulos (ADR-006: module-entry como library).
// Cada módulo expõe <MOD>_MODULE_DESCRIPTOR via @journeyos/<mod> (lib shell-entry).
import { Routes } from '@angular/router';
import { WRKS_MODULE_DESCRIPTOR } from '@journeyos/wrks';

export interface ModuleDescriptor {
  key: string;
  basePath: string;
  loadChildren: () => Promise<unknown>;
  metadata?: unknown;
  flags?: unknown;
  permissionMap?: unknown;
}

export const MODULE_DESCRIPTORS: ModuleDescriptor[] = [
  WRKS_MODULE_DESCRIPTOR,
];

/** Rotas lazy derivadas dos descritores. */
export const moduleRoutes: Routes = MODULE_DESCRIPTORS.map((d) => ({
  path: d.basePath,
  loadChildren: d.loadChildren as never,
}));
