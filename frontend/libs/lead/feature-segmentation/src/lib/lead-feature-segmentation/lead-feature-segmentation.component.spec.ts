import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadFeatureSegmentationComponent } from './lead-feature-segmentation.component';

describe('LeadFeatureSegmentationComponent', () => {
  let component: LeadFeatureSegmentationComponent;
  let fixture: ComponentFixture<LeadFeatureSegmentationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadFeatureSegmentationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadFeatureSegmentationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
