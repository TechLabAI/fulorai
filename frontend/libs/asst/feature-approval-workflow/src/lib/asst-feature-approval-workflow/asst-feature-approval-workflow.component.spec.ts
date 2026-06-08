import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstFeatureApprovalWorkflowComponent } from './asst-feature-approval-workflow.component';

describe('AsstFeatureApprovalWorkflowComponent', () => {
  let component: AsstFeatureApprovalWorkflowComponent;
  let fixture: ComponentFixture<AsstFeatureApprovalWorkflowComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstFeatureApprovalWorkflowComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstFeatureApprovalWorkflowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
