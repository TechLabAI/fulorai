import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureDecisionLogComponent } from './jrny-feature-decision-log.component';

describe('JrnyFeatureDecisionLogComponent', () => {
  let component: JrnyFeatureDecisionLogComponent;
  let fixture: ComponentFixture<JrnyFeatureDecisionLogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureDecisionLogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureDecisionLogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
