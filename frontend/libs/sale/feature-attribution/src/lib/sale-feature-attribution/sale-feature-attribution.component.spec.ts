import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeatureAttributionComponent } from './sale-feature-attribution.component';

describe('SaleFeatureAttributionComponent', () => {
  let component: SaleFeatureAttributionComponent;
  let fixture: ComponentFixture<SaleFeatureAttributionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeatureAttributionComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeatureAttributionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
