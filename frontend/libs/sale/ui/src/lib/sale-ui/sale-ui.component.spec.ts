import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleUiComponent } from './sale-ui.component';

describe('SaleUiComponent', () => {
  let component: SaleUiComponent;
  let fixture: ComponentFixture<SaleUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
