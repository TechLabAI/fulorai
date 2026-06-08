import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksFeatureEmpresaSelectComponent } from './wrks-feature-empresa-select.component';

describe('WrksFeatureEmpresaSelectComponent', () => {
  let component: WrksFeatureEmpresaSelectComponent;
  let fixture: ComponentFixture<WrksFeatureEmpresaSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksFeatureEmpresaSelectComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksFeatureEmpresaSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
