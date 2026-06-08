import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksFeatureWorkspaceComponent } from './wrks-feature-workspace.component';

describe('WrksFeatureWorkspaceComponent', () => {
  let component: WrksFeatureWorkspaceComponent;
  let fixture: ComponentFixture<WrksFeatureWorkspaceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksFeatureWorkspaceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksFeatureWorkspaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
