import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureQualificationRulesComponent } from './lead-feature-qualification-rules.component';

describe('LeadFeatureQualificationRulesComponent', () => {
  let component: LeadFeatureQualificationRulesComponent;
  let fixture: ComponentFixture<LeadFeatureQualificationRulesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureQualificationRulesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureQualificationRulesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
