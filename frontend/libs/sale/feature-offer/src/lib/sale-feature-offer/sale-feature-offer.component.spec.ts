import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeatureOfferComponent } from './sale-feature-offer.component';

describe('SaleFeatureOfferComponent', () => {
  let component: SaleFeatureOfferComponent;
  let fixture: ComponentFixture<SaleFeatureOfferComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeatureOfferComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeatureOfferComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
