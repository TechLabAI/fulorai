import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleStylesComponent } from './sale-styles.component';

describe('SaleStylesComponent', () => {
  let component: SaleStylesComponent;
  let fixture: ComponentFixture<SaleStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
