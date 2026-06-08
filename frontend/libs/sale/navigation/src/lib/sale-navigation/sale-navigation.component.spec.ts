import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleNavigationComponent } from './sale-navigation.component';

describe('SaleNavigationComponent', () => {
  let component: SaleNavigationComponent;
  let fixture: ComponentFixture<SaleNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
