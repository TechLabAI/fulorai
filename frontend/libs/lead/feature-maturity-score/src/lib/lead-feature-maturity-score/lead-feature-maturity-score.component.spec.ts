import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureMaturityScoreComponent } from './lead-feature-maturity-score.component';

describe('LeadFeatureMaturityScoreComponent', () => {
  let component: LeadFeatureMaturityScoreComponent;
  let fixture: ComponentFixture<LeadFeatureMaturityScoreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureMaturityScoreComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureMaturityScoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
