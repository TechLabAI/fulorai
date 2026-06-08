import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleAccessComponent } from './sale-access.component';

describe('SaleAccessComponent', () => {
  let component: SaleAccessComponent;
  let fixture: ComponentFixture<SaleAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
