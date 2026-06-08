import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlAccessComponent } from './intl-access.component';

describe('IntlAccessComponent', () => {
  let component: IntlAccessComponent;
  let fixture: ComponentFixture<IntlAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
