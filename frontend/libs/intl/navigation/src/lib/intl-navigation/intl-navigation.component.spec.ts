import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlNavigationComponent } from './intl-navigation.component';

describe('IntlNavigationComponent', () => {
  let component: IntlNavigationComponent;
  let fixture: ComponentFixture<IntlNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
