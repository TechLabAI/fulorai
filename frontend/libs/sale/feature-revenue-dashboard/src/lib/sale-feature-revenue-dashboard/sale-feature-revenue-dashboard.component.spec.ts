import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeatureRevenueDashboardComponent } from './sale-feature-revenue-dashboard.component';

describe('SaleFeatureRevenueDashboardComponent', () => {
  let component: SaleFeatureRevenueDashboardComponent;
  let fixture: ComponentFixture<SaleFeatureRevenueDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeatureRevenueDashboardComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeatureRevenueDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
