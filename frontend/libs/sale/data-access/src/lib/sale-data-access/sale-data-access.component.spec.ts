import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleDataAccessComponent } from './sale-data-access.component';

describe('SaleDataAccessComponent', () => {
  let component: SaleDataAccessComponent;
  let fixture: ComponentFixture<SaleDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
