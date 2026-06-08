import { Routes } from '@angular/router';
import { AppShellComponent } from './shell/app-shell.component';
import { moduleRoutes } from './config/module-descriptors';

export const appRoutes: Routes = [
  {
    path: '',
    component: AppShellComponent,
    children: [
      ...moduleRoutes,
      { path: '**', redirectTo: '' },
    ],
  },
];
