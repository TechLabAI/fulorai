import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlDataAccessComponent } from './intl-data-access.component';

describe('IntlDataAccessComponent', () => {
  let component: IntlDataAccessComponent;
  let fixture: ComponentFixture<IntlDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
