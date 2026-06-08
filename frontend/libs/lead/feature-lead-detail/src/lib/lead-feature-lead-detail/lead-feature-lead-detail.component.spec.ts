import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureLeadDetailComponent } from './lead-feature-lead-detail.component';

describe('LeadFeatureLeadDetailComponent', () => {
  let component: LeadFeatureLeadDetailComponent;
  let fixture: ComponentFixture<LeadFeatureLeadDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureLeadDetailComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureLeadDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
