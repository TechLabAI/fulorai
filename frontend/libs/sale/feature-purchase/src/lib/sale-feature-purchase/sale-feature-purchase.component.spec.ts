import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeaturePurchaseComponent } from './sale-feature-purchase.component';

describe('SaleFeaturePurchaseComponent', () => {
  let component: SaleFeaturePurchaseComponent;
  let fixture: ComponentFixture<SaleFeaturePurchaseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeaturePurchaseComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeaturePurchaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
