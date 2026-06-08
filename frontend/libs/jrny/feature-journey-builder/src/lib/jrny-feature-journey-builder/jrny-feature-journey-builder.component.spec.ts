import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureJourneyBuilderComponent } from './jrny-feature-journey-builder.component';

describe('JrnyFeatureJourneyBuilderComponent', () => {
  let component: JrnyFeatureJourneyBuilderComponent;
  let fixture: ComponentFixture<JrnyFeatureJourneyBuilderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureJourneyBuilderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureJourneyBuilderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
