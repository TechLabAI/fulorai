import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureLeadListComponent } from './lead-feature-lead-list.component';

describe('LeadFeatureLeadListComponent', () => {
  let component: LeadFeatureLeadListComponent;
  let fixture: ComponentFixture<LeadFeatureLeadListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureLeadListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureLeadListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
