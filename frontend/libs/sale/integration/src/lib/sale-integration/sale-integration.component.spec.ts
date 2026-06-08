import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleIntegrationComponent } from './sale-integration.component';

describe('SaleIntegrationComponent', () => {
  let component: SaleIntegrationComponent;
  let fixture: ComponentFixture<SaleIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
