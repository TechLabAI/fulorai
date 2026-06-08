import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureSurveyComponent } from './lead-feature-survey.component';

describe('LeadFeatureSurveyComponent', () => {
  let component: LeadFeatureSurveyComponent;
  let fixture: ComponentFixture<LeadFeatureSurveyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureSurveyComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureSurveyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
