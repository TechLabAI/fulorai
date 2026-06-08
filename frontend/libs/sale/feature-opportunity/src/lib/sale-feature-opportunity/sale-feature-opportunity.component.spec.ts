import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeatureOpportunityComponent } from './sale-feature-opportunity.component';

describe('SaleFeatureOpportunityComponent', () => {
  let component: SaleFeatureOpportunityComponent;
  let fixture: ComponentFixture<SaleFeatureOpportunityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeatureOpportunityComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeatureOpportunityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
