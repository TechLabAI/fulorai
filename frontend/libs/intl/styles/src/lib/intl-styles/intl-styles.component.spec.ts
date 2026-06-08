import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlStylesComponent } from './intl-styles.component';

describe('IntlStylesComponent', () => {
  let component: IntlStylesComponent;
  let fixture: ComponentFixture<IntlStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
