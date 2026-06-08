import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlUiComponent } from './intl-ui.component';

describe('IntlUiComponent', () => {
  let component: IntlUiComponent;
  let fixture: ComponentFixture<IntlUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
