import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureJourneyAnalyticsComponent } from './jrny-feature-journey-analytics.component';

describe('JrnyFeatureJourneyAnalyticsComponent', () => {
  let component: JrnyFeatureJourneyAnalyticsComponent;
  let fixture: ComponentFixture<JrnyFeatureJourneyAnalyticsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureJourneyAnalyticsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureJourneyAnalyticsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
