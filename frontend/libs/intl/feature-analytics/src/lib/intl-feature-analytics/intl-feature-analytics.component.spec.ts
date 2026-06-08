import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntlFeatureAnalyticsComponent } from './intl-feature-analytics.component';

describe('IntlFeatureAnalyticsComponent', () => {
  let component: IntlFeatureAnalyticsComponent;
  let fixture: ComponentFixture<IntlFeatureAnalyticsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IntlFeatureAnalyticsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(IntlFeatureAnalyticsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
